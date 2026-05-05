// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::StorageVolumePostTarget;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageVolumeSnapshotPost {
    pub name: String,

    pub migration: bool,

    pub target: Option<StorageVolumePostTarget>,

}