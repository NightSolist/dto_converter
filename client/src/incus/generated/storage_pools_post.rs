// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StoragePoolsPost {
    pub name: String,

    pub driver: String,

    pub config: ConfigMap,

    pub description: String,

}