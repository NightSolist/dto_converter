// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StoragePool {
    pub name: String,

    pub driver: String,

    pub usedby: Vec<String>,

    pub status: String,

    pub locations: Vec<String>,

    pub config: ConfigMap,

    pub description: String,

}