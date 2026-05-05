// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ImagesPostSource {
    pub mode: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub url: String,

    pub name: String,

    pub fingerprint: String,

    pub secret: String,

    pub project: String,

    pub alias: String,

    pub certificate: String,

    pub protocol: String,

    pub server: String,

    pub imagetype: String,

}