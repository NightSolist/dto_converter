// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use serde_json;use crate::incus::ResponseType;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Response {
    #[serde(rename = "type")]    pub r#type: ResponseType,

    pub status: String,

    pub statuscode: i64,

    pub operation: String,

    pub code: i64,

    pub error: String,

    pub metadata: serde_json::Value,

}