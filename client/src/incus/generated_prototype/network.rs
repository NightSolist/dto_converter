// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Network {
    pub name: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub usedby: Vec<String>,

    pub managed: bool,

    pub status: String,

    pub locations: Vec<String>,

    pub project: String,

    pub config: ConfigMap,

    pub description: String,

}