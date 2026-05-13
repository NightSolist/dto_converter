package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
	"strings"
)

type Package struct {
	Name    string   `json:"name"`
	Structs []Struct `json:"structs"`
	Enums   []Enum   `json:"enums"`
	Aliases []Alias  `json:"aliases"`
}

type Struct struct {
	Name     string   `json:"name"`
	Comment  string   `json:"comment"`
	Fields   []Field  `json:"fields"`
	Embedded []string `json:"embedded"`
}

type Field struct {
	Name string `json:"name"`
	Type string `json:"type"`
	Tag  string `json:"tag"`
}

type Enum struct {
	Name   string      `json:"name"`
	Type   string      `json:"type"`
	Values []EnumValue `json:"values"`
}

type EnumValue struct {
	Name  string `json:"name"`
	Value string `json:"value"`
}

type Alias struct {
	Name string `json:"name"`
	Type string `json:"type"`
}

func main() {
	dirPath := flag.String("dir", "", "Path to go package directory")
	flag.Parse()

	if *dirPath == "" {
		fmt.Println("Usage: go-ast-parser -dir <path>")
		os.Exit(1)
	}

	fset := token.NewFileSet()
	pkgs, err := parser.ParseDir(fset, *dirPath, nil, parser.ParseComments)
	if err != nil {
		panic(err)
	}

	var result []Package

	for pkgName, pkg := range pkgs {
		p := Package{Name: pkgName}
		enumMap := make(map[string]*Enum)

		// PASS 1: Collect Types
		for _, file := range pkg.Files {
			ast.Inspect(file, func(n ast.Node) bool {
				if ts, ok := n.(*ast.TypeSpec); ok {
					// Struct
					if st, ok := ts.Type.(*ast.StructType); ok {
						s := Struct{
							Name:    ts.Name.Name,
							Comment: ts.Doc.Text(),
						}
						for _, field := range st.Fields.List {
							fieldType := getTypeName(field.Type)
							tag := ""
							if field.Tag != nil {
								tag = strings.Trim(field.Tag.Value, "`")
							}
							if len(field.Names) == 0 {
								s.Embedded = append(s.Embedded, fieldType)
							} else {
								for _, name := range field.Names {
									s.Fields = append(s.Fields, Field{
										Name: name.Name,
										Type: fieldType,
										Tag:  tag,
									})
								}
							}
						}
						p.Structs = append(p.Structs, s)
						return true
					}

					// Alias or Enum Base
					typeName := ts.Name.Name
					baseType := getTypeName(ts.Type)

					// Любой type X Y, где Y не struct/interface, считаем кандидатом
					// Если это map/slice — точно Alias
					if strings.HasPrefix(baseType, "map[") || strings.HasPrefix(baseType, "[]") {
						p.Aliases = append(p.Aliases, Alias{Name: typeName, Type: baseType})
						return true
					}

					// Иначе (string, int, float, bool) — кандидат в Enum или Alias
					// Регистрируем, потом разберемся (есть ли константы)
					if _, exists := enumMap[typeName]; !exists {
						enumMap[typeName] = &Enum{Name: typeName, Type: baseType}
					}
				}
				return true
			})
		}

		// PASS 2: Collect Constants
		for _, file := range pkg.Files {
			ast.Inspect(file, func(n ast.Node) bool {
				if gd, ok := n.(*ast.GenDecl); ok && gd.Tok == token.CONST {
					var lastType string
					for _, spec := range gd.Specs {
						vs, ok := spec.(*ast.ValueSpec)
						if !ok {
							continue
						}

						typeName := ""
						if vs.Type != nil {
							typeName = getTypeName(vs.Type)
							lastType = typeName
						} else if len(vs.Values) > 0 {
							// Попытка определить тип из приведения: MyType("val")
							if call, ok := vs.Values[0].(*ast.CallExpr); ok {
								typeName = getTypeName(call.Fun)
								lastType = typeName
							} else {
								typeName = lastType
							}
						} else {
							typeName = lastType
						}

						if enum, exists := enumMap[typeName]; exists {
							for i, name := range vs.Names {
								val := "0"
								if i < len(vs.Values) {
									if bl, ok := vs.Values[i].(*ast.BasicLit); ok {
										val = bl.Value
									} else if ident, ok := vs.Values[i].(*ast.Ident); ok {
										val = ident.Name
									} else if call, ok := vs.Values[i].(*ast.CallExpr); ok {
										if len(call.Args) > 0 {
											if bl, ok := call.Args[0].(*ast.BasicLit); ok {
												val = bl.Value
											}
										}
									}
								}
								enum.Values = append(enum.Values, EnumValue{
									Name:  name.Name,
									Value: val,
								})
							}
						}
					}
				}
				return true
			})
		}

		// Finalize
		for typeName, e := range enumMap {
			if len(e.Values) > 0 {
				p.Enums = append(p.Enums, *e)
			} else {
				// Если констант нет, это Alias (например type ID string)
				p.Aliases = append(p.Aliases, Alias{Name: typeName, Type: e.Type})
			}
		}

		result = append(result, p)
	}

	bytes, _ := json.MarshalIndent(result, "", "  ")
	fmt.Println(string(bytes))
}

func getTypeName(expr ast.Expr) string {
	if expr == nil {
		return ""
	}
	switch t := expr.(type) {
	case *ast.Ident:
		return t.Name
	case *ast.StarExpr:
		return "*" + getTypeName(t.X)
	case *ast.ArrayType:
		return "[]" + getTypeName(t.Elt)
	case *ast.MapType:
		return "map[" + getTypeName(t.Key) + "]" + getTypeName(t.Value)
	case *ast.SelectorExpr:
		return getTypeName(t.X) + "." + t.Sel.Name
	default:
		return fmt.Sprintf("%v", t)
	}
}
