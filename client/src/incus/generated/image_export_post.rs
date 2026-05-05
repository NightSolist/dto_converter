// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ImageAlias;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ImageExportPost {
    pub target: String,

    pub secret: String,

    pub certificate: String,

    pub aliases: Vec<ImageAlias>,

    pub project: String,

    pub profiles: Vec<String>,

}