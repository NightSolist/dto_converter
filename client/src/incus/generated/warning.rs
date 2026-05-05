// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Warning {
    pub uuid: String,

    pub location: String,

    pub project: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub count: i64,

    pub firstseenat: chrono::DateTime<chrono::Utc>,

    pub lastseenat: chrono::DateTime<chrono::Utc>,

    pub lastmessage: String,

    pub severity: String,

    pub entityurl: String,

    pub status: String,

}