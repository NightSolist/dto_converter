use std::collections::HashMap;

pub struct RemoteConfig {
    pub url: String,
    pub protocol: String,
}

pub fn get_default_remotes() -> HashMap<String, RemoteConfig> {
    let mut remotes = HashMap::new();
    
    remotes.insert("images".to_string(), RemoteConfig {
        url: "https://images.linuxcontainers.org".to_string(),
        protocol: "simplestreams".to_string(),
    });

    remotes.insert("ubuntu".to_string(), RemoteConfig {
        url: "https://cloud-images.ubuntu.com/releases".to_string(),
        protocol: "simplestreams".to_string(),
    });

    remotes.insert("local".to_string(), RemoteConfig {
        url: "".to_string(), // Локальный
        protocol: "incus".to_string(),
    });

    remotes
}

pub fn parse_image(image_str: &str) -> (String, String, String) {
    let remotes = get_default_remotes();
    
    if let Some((remote_name, alias)) = image_str.split_once(':') {
        if let Some(config) = remotes.get(remote_name) {
            return (config.url.clone(), config.protocol.clone(), alias.to_string());
        }
    }

    // Если remote не найден или не указан — считаем локальным (или ошибка)
    // Для простоты вернем local behavior (пустой url)
    ("".to_string(), "".to_string(), image_str.to_string())
}