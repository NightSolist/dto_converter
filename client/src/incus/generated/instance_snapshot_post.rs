// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::InstancePostTarget;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstanceSnapshotPost {
    pub name: String,

    pub migration: bool,

    pub target: Option<InstancePostTarget>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub live: Option<bool>,

}