// Auto-generated. Do not edit.

use serde::{Deserialize, Deserializer};
use serde_json::Value;
use std::collections::HashMap;

/// Автоматически сгенерированный аналог Go-типа DevicesMap.
/// При десериализации JSON bool/number/null во вложенных словарях
/// приводятся к строке.
pub type DevicesMap = HashMap<String, HashMap<String, String>>;

pub fn deserialize_devices_map<'de, D>(
    deserializer: D,
) -> Result<DevicesMap, D::Error>
where
    D: Deserializer<'de>,
{
    let raw = HashMap::<String, HashMap<String, Value>>::deserialize(
        deserializer,
    )?;
    let mut outer = HashMap::new();

    for (device_name, device_cfg) in raw {
        let mut inner = HashMap::new();
        for (key, value) in device_cfg {
            let string_value = match value {
                Value::String(s) => s,
                Value::Bool(b) => b.to_string(),
                Value::Number(n) => n.to_string(),
                Value::Null => String::new(),
                _ => {
                    return Err(serde::de::Error::custom(format!(
                        "unsupported value type for key '{}' \
                         in device '{}'",
                        key, device_name
                    )))
                }
            };
            inner.insert(key, string_value);
        }
        outer.insert(device_name, inner);
    }

    Ok(outer)
}

pub fn deserialize_option_devices_map<'de, D>(
    deserializer: D,
) -> Result<Option<DevicesMap>, D::Error>
where
    D: Deserializer<'de>,
{
    let opt = Option::<HashMap<String, HashMap<String, Value>>>::deserialize(
        deserializer,
    )?;

    match opt {
        None => Ok(None),
        Some(raw_outer) => {
            let mut outer = HashMap::new();
            for (device_name, device_cfg) in raw_outer {
                let mut inner = HashMap::new();
                for (key, value) in device_cfg {
                    let string_value = match value {
                        Value::String(s) => s,
                        Value::Bool(b) => b.to_string(),
                        Value::Number(n) => n.to_string(),
                        Value::Null => String::new(),
                        _ => {
                            return Err(serde::de::Error::custom(
                                format!(
                                    "unsupported value type for key '{}' \
                                     in device '{}'",
                                    key, device_name
                                ),
                            ))
                        }
                    };
                    inner.insert(key, string_value);
                }
                outer.insert(device_name, inner);
            }
            Ok(Some(outer))
        }
    }
}