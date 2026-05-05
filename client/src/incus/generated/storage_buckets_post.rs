// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageBucketsPost {
    pub name: String,

    pub config: ConfigMap,

    pub description: String,

}