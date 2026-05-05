// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageVolumeStateUsage {
    #[serde(skip_serializing_if = "Option::is_none")]    pub used: Option<u64>,

    pub total: i64,

}