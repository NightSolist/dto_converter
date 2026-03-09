use serde::Deserialize;
use std::collections::HashMap;

#[derive(Debug, Deserialize)]
pub struct Lab {
    pub name: String,
    #[serde(default)]
    pub instances: Vec<InstanceConfig>,
}

#[derive(Debug, Deserialize)]
pub struct InstanceConfig {
    pub name: String,
    #[serde(rename = "type")]
    pub type_: String,
    pub image: String,
    #[serde(default)]
    pub profiles: Vec<String>,
    #[serde(default)]
    pub config: HashMap<String, String>,
    #[serde(default)]
    pub start: bool,
}