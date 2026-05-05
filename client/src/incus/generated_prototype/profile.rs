// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;
use crate::incus::DevicesMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Profile {
    pub name: String,

    pub usedby: Vec<String>,

    pub project: String,

    pub config: ConfigMap,

    pub description: String,

    pub devices: DevicesMap,

}