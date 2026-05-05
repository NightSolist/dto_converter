// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkZone {
    pub name: String,

    pub usedby: Vec<String>,

    pub project: String,

    pub description: String,

    pub config: ConfigMap,

}