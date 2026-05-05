// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::StorageVolumeSource;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InitStorageVolumesProjectPost {
    pub pool: String,

    pub project: String,

    pub name: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub source: StorageVolumeSource,

    pub contenttype: String,

}