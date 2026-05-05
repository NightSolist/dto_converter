// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageVolumePut {
    pub config: ConfigMap,

    pub description: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub restore: Option<String>,

}