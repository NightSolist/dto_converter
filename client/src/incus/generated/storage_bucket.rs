// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageBucket {
    pub name: String,

    pub s3url: String,

    pub location: String,

    pub project: String,

    pub config: ConfigMap,

    pub description: String,

}