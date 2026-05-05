// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;use crate::incus::ImageAlias;
use crate::incus::ImageSource;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Image {
    pub aliases: Vec<ImageAlias>,

    pub architecture: String,

    pub cached: bool,

    pub filename: String,

    pub fingerprint: String,

    pub size: i64,

    pub updatesource: Option<ImageSource>,

    #[serde(rename = "type")]    pub r#type: String,

    pub createdat: chrono::DateTime<chrono::Utc>,

    pub lastusedat: chrono::DateTime<chrono::Utc>,

    pub uploadedat: chrono::DateTime<chrono::Utc>,

    pub project: String,

    pub autoupdate: bool,

    pub properties: HashMap<String, String>,

    pub public: bool,

    pub expiresat: chrono::DateTime<chrono::Utc>,

    pub profiles: Vec<String>,

}