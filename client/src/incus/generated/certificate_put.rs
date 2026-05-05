// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct CertificatePut {
    pub name: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub restricted: bool,

    pub projects: Vec<String>,

    pub certificate: String,

    pub description: String,

}