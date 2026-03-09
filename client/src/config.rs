use serde::Deserialize;
use std::collections::HashMap;

#[derive(Debug, Deserialize)]
pub struct Lab {
    pub name: String,
    pub description: Option<String>,
    #[serde(default)]
    pub networks: Vec<NetworkConfig>,
    #[serde(default)]
    pub instances: Vec<InstanceConfig>,
}

#[derive(Debug, Deserialize)]
pub struct NetworkConfig {
    pub name: String,
    pub ipv4: Option<String>,
    pub ipv6: Option<String>,
    pub dns_domain: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct InstanceConfig {
    pub name: String,
    #[serde(rename = "type")]
    pub type_: String,
    pub image: String,
    pub network: Option<String>,
    #[serde(default)]
    pub profiles: Vec<String>,
    #[serde(default)]
    pub config: HashMap<String, String>,
    #[serde(default)]
    pub start: bool,
}