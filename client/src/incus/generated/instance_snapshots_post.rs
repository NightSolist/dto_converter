// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstanceSnapshotsPost {
    pub name: String,

    pub stateful: bool,

    pub expiresat: Option<chrono::DateTime<chrono::Utc>>,

}