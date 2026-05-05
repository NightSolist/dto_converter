// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworksPost {
    pub name: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub config: ConfigMap,

    pub description: String,

}