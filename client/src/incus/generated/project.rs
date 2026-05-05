// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Project {
    pub name: String,

    pub usedby: Vec<String>,

    pub config: ConfigMap,

    pub description: String,

}