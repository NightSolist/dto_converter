// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstanceBackup {
    pub name: String,

    pub createdat: chrono::DateTime<chrono::Utc>,

    pub expiresat: chrono::DateTime<chrono::Utc>,

    pub instanceonly: bool,

    pub optimizedstorage: bool,

}