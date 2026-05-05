// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct CertificateAddToken {
    pub clientname: String,

    pub fingerprint: String,

    pub addresses: Vec<String>,

    pub secret: String,

    pub expiresat: chrono::DateTime<chrono::Utc>,

}