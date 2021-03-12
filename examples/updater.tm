# We start with the version of the TMSpec language that we use
version 0.0;

# Then we define the trust zones
zone @update_maker: default;
zone cloud: default;
zone @update_server;
zone @device;

# We define all components and specify which trust zone they are in
component update_maker(externalentity): zone=@update_maker;
component update_repository(datastore): zone=@update_server;
component update_server(process): zone=@update_server;
component update_loader(process): zone=@device;
component update_store(datastore): zone=@device;
component update_installer(process): zone=@device;
component firmware(datastore): zone=@device;
component pubkeys(datastore): zone=@device;
component mailserver(externalentity): zone=cloud;

# And the flows between the components
flow publish_update: update_maker --> update_repository, label='publish update';
flow retrieve_update: update_repository --> update_server;
flow request_update: update_server <-- update_loader;
flow get_update: update_server --> update_loader;
flow store_update: update_loader --> update_store;
flow check_update: update_loader <-- update_store;
flow load_update: update_store --> update_installer;
flow write_update: update_installer --> firmware;
flow auth_check_pubkey: pubkeys --> update_loader;
flow send_mail: update_loader --> mailserver;
