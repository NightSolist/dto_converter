// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::StorageVolumeStateUsage;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageVolumeState {
    pub usage: Option<StorageVolumeStateUsage>,

}