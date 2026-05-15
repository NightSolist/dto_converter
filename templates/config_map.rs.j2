// Auto-generated. Do not edit.

use serde::{Deserialize, Deserializer};
use serde_json::Value;
use std::collections::HashMap;

/// Автоматически сгенерированный аналог Go-типа ConfigMap.
/// При десериализации JSON bool/number/null приводятся к строке,
/// воспроизводя поведение UnmarshalJSON из Go-реализации.
pub type ConfigMap = HashMap<String, String>;

pub fn deserialize_config_map<'de, D>(
    deserializer: D,
) -> Result<ConfigMap, D::Error>
where
    D: Deserializer<'de>,
{
    let raw = HashMap::<String, Value>::deserialize(deserializer)?;
    let mut result = HashMap::new();

    for (key, value) in raw {
        let string_value = match value {
            Value::String(s) => s,
            Value::Bool(b) => b.to_string(),
            Value::Number(n) => n.to_string(),
            Value::Null => String::new(),
            _ => {
                return Err(serde::de::Error::custom(format!(
                    "unsupported value type for key '{}' in ConfigMap",
                    key
                )))
            }
        };
        result.insert(key, string_value);
    }

    Ok(result)
}

pub fn deserialize_option_config_map<'de, D>(
    deserializer: D,
) -> Result<Option<ConfigMap>, D::Error>
where
    D: Deserializer<'de>,
{
    let opt = Option::<HashMap<String, Value>>::deserialize(
        deserializer,
    )?;

    match opt {
        None => Ok(None),
        Some(raw) => {
            let mut result = HashMap::new();
            for (key, value) in raw {
                let string_value = match value {
                    Value::String(s) => s,
                    Value::Bool(b) => b.to_string(),
                    Value::Number(n) => n.to_string(),
                    Value::Null => String::new(),
                    _ => {
                        return Err(serde::de::Error::custom(
                            format!(
                                "unsupported value type for key '{}' \
                                 in ConfigMap",
                                key
                            ),
                        ))
                    }
                };
                result.insert(key, string_value);
            }
            Ok(Some(result))
        }
    }
}