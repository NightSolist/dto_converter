// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;use crate::incus::ImageAlias;
use crate::incus::ImagesPostSource;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ImagesPost {
    pub filename: String,

    pub source: Option<ImagesPostSource>,

    pub compressionalgorithm: String,

    pub format: String,

    pub aliases: Vec<ImageAlias>,

    pub autoupdate: bool,

    pub properties: HashMap<String, String>,

    pub public: bool,

    pub expiresat: chrono::DateTime<chrono::Utc>,

    pub profiles: Vec<String>,

}