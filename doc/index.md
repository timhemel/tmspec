# TMSpec

TMSpec lets you specify a data flow diagram of an architecture, annotate it with properties, such as trust zones and technologies, and analyze the model according to (customizable) rules.
It is completely text based, letting you store the threat model in version control and run the analysis from scripts. This makes it easy to fit in a DevOps environment or CI/CD pipeline.

## How does it work?

You start by describing your data flow diagram in the TMSpec language.
The analysis will give you three kinds of responses: *errors*, *questions* and *threats*.

An error means that you data flow diagram has an error of some sort. This could be a syntactic
error, such as a typing mistake, or a semantic error, such as specifying a diagram that does
not make any sense.

A question means that TMSpec needs to know more information about the architecture. Usually this
is a missing property of any of the data flow elements.

A threat is a potential vulnerability or weakness that may exist in your architecture.

For errors and questions, change the data flow diagram and run the analysis again. Hopefully the
errors have disappeared, but answering the questions could lead to more threats, or to more questions.
Keep adding the required information until there are no more errors and questions, and only threats will
remain.

TMSpec will not keep track of whether you have mitigated any threats, it will only report threats that result
from the architectural analysis. The analysis is rule-based, which means that TMSpec can only detect threats that
it knows about. You can teach TMSpec new rules by adding them to a rules database.

As with any security scanner, TMSpec may report threats that do not apply. If you find any corner cases where certain
rules do not apply, you can change the rule.


## Example

```
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
```

TODO: run with threatlib


