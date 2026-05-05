// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkIntegration {
    pub name: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub usedby: Vec<String>,

    pub description: String,

    pub config: ConfigMap,

}