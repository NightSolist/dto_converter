// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkPeer {
    pub name: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub targetproject: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub targetnetwork: Option<String>,

    pub status: String,

    pub usedby: Vec<String>,

    #[serde(rename = "type")]    pub r#type: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub targetintegration: Option<String>,

    pub description: String,

    pub config: ConfigMap,

}