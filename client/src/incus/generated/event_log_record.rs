// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use serde_json;
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct EventLogRecord {
    pub time: chrono::DateTime<chrono::Utc>,

    pub lvl: String,

    pub msg: String,

    pub ctx: Vec<serde_json::Value>,

}