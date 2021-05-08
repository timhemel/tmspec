% STRIDE per element
%
%

prop_valid(X,stores_logs,yes) :- datastore(X).
prop_valid(X,stores_logs,no) :- datastore(X).
prop_text(X,stores_logs,yes,'The datastore contains log information.') :- datastore(X).
prop_text(X,stores_logs,no,'The datastore does not contain log information.') :- datastore(X).

threat_descr(['stride-per-element',spoof_external_entity,0],
  'Spoof external entity',
  'An attacker pretends to be the external entity $v1.').
threat(['stride-per-element',spoof_external_entity,0],[P]) :- externalentity(P).

threat_descr(['stride-per-element',spoof_process,0],'Spoof process','An attacker spoofs process $v1.').
threat(['stride-per-element',spoof_process,0],[P]) :- process(P).

threat_descr(['stride-per-element',tamper_process,0],'Tamper process','An attacker tampers with process $v1.').
threat(['stride-per-element',tamper_process,0],[P]) :- process(P).

threat_descr(['stride-per-element',tamper_datastore,0],'Tamper datastore','An attacker tampers with datastore $v1.').
threat(['stride-per-element',tamper_datastore,0],[P]) :- datastore(P).

threat_descr(['stride-per-element',tamper_dataflow,0],'Tamper dataflow','An attacker tampers with the data sent through the dataflow $v1 (from $v2 to $v3).').
threat(['stride-per-element',tamper_dataflow,0],[P,X,Y]) :- dataflow(P,X,Y).

threat_descr(['stride-per-element',repudiation_external_entity,0],'Repudiation on external entity','External entity $v1 can claim or deny something and you cannot prove or refute it.').
threat(['stride-per-element',repudiation_external_entity,0],[P]) :- external_entity(P).

threat_descr(['stride-per-element',repudiation_process,0],'Repudiation on process','Someone claims that an action in process $v1 did not happen.').
threat(['stride-per-element',repudiation_process,0],[P]) :- process(P).

threat_descr(['stride-per-element',repudiation_datastore,0],'Repudiation on datastore','An attacker attacks the logs stored in the datastore.').
threat(['stride-per-element',repudiation_datastore,0],[P]) :- datastore(P), property(P,stores_logs,yes).

threat_descr(['stride-per-element',information_disclosure_process,0],
  'Information disclosure on process',
  'Process $v1 leaks information that is sensitive or that may help an attacker.').
threat(['stride-per-element',information_disclosure_process,0],[P]) :- process(P).

threat_descr(['stride-per-element',information_disclosure_datastore,0],
  'Information disclosure on datastore',
  'An attacker sees information from datastore $v1 that is sensitive or may help further attacks.').
threat(['stride-per-element',information_disclosure_datastore,0],[P]) :- datastore(P).

threat_descr(['stride-per-element',information_disclosure_dataflow,0],
  'Information disclosure on dataflow',
  'An attacker obtains information from dataflow $v1 ($v2 --> $v3) that is sensitive or may help further attacks.').
threat(['stride-per-element',information_disclosure_dataflow,0],[P,X,Y]) :- dataflow(P,X,Y).

threat_descr(['stride-per-element',denial_of_service_process,0],'Denial of service on process','An attacker makes process $v1 unavailable.').
threat(['stride-per-element',denial_of_service_process,0],[P]) :- process(P).

threat_descr(['stride-per-element',denial_of_service_datastore,0],'Denial of service on datastore','An attacker makes datastore $v1 unavailable.').
threat(['stride-per-element',denial_of_service_datastore,0],[P]) :- datastore(P).

threat_descr(['stride-per-element',denial_of_service_dataflow,0],
  'Denial of service on dataflow',
  'An attacker makes it (partially) impossible to send or receive data via dataflow $v1 ($v2 --> $v3).').
threat(['stride-per-element',denial_of_service_dataflow,0],[P,X,Y]) :- dataflow(P,X,Y).

threat_descr(['stride-per-element',elevation_of_privilege_process,0],
  'Elevation of privilege on process',
  'Attackers can make process $v1 do something\nthat they are not allowed to do.').
threat(['stride-per-element',elevation_of_privilege_process,0],[P]) :- process(P).
 
