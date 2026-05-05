// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;use serde_json;use crate::incus::StatusCode;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Operation {
    pub id: String,

    pub class: String,

    pub description: String,

    pub createdat: chrono::DateTime<chrono::Utc>,

    pub updatedat: chrono::DateTime<chrono::Utc>,

    pub status: String,

    pub statuscode: StatusCode,

    pub resources: HashMap<String, Vec<String>>,

    pub metadata: HashMap<String, serde_json::Value>,

    pub maycancel: bool,

    pub err: String,

    pub location: String,

}