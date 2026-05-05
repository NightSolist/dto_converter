// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;
use crate::incus::StorageVolumeSource;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageVolumesPost {
    pub name: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub source: StorageVolumeSource,

    pub contenttype: String,

    pub config: ConfigMap,

    pub description: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub restore: Option<String>,

}