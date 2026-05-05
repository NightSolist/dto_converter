// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkAddressSet {
    pub usedby: Vec<String>,

    pub project: String,

    pub addresses: Vec<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub config: Option<ConfigMap>,

    pub description: String,

    pub name: String,

}