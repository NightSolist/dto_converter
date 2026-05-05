// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::StorageVolumePostTarget;
use crate::incus::StorageVolumeSource;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageVolumePost {
    pub name: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub pool: Option<String>,

    pub migration: bool,

    pub target: Option<StorageVolumePostTarget>,

    pub volumeonly: bool,

    #[serde(skip_serializing_if = "Option::is_none")]    pub project: Option<String>,

    pub source: StorageVolumeSource,

}