// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;
use crate::incus::DevicesMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InitProfileProjectPost {
    pub project: String,

    pub name: String,

    pub config: ConfigMap,

    pub description: String,

    pub devices: DevicesMap,

}