# Restricted transaction-data request — 18 exact datasets

**UN Peace Operations Efficiency | Request specification, 8 October 2026**

## Purpose and limitations

Request only the transaction evidence needed to verify three already documented coordination arrangements: (1) UNIFIL-to-UNSCOL assets; (2) BINUH-to-UNSOH aviation and support-service charges; and (3) RSCE / Kuwait Joint Support Office client, staffing and financial allocations. The current public budget documents do not prove realized savings or duplicate charges.

**Requested actuals:** from **1 January 2025 through the most recently closed accounting month**. Include outstanding 2026 commitments and **planned 2027 asset movements, contractual commitments and approved budget actions**, clearly marked as planned rather than actual. If records are not retained back to January 2025, state the earliest complete date available.

## Exact requested records and columns

| Request ID | Mission / service entities | Dataset | Minimum record-level columns |
|---|---|---|---|
| REQ01 | UNIFIL / UNSCOL | UNIFIL outgoing assets | asset_id;VIN_or_serial;asset_class;book_value;location;service_life;inventory_date |
| REQ02 | UNIFIL / UNSCOL | signed release acceptance | asset_id;transfer_document_id;release_date;receipt_date;source;destination;quantity;condition |
| REQ03 | UNIFIL / UNSCOL | asset GL and disposal entries | asset_id;posting_date;document;fund;cost_center;transfer_value;account |
| REQ04 | UNIFIL / UNSCOL | purchase requisitions PO cancellations | requisition;PO;vendor;planned_price;cancel_date;committed_liability;period |
| REQ05 | UNIFIL / UNSCOL | transport refurbishment security costs | invoice;transport;security;repairs;installation;amount;date;fund |
| REQ06 | UNIFIL / UNSCOL | ration lots goods movement | stock_lot;expiry;quantity_issued;quantity_received;goods_receipt;issue_note;value |
| REQ07 | BINUH / UNSOH | intermission signed SLA | SLA_id;signatures;effective_date;service_scope;tariffs;performance_metrics |
| REQ08 | BINUH / UNSOH | monthly billing AR AP | charge_id;invoice;service_start;service_end;BINUH_AP;UNSOH_AR;amount;fund |
| REQ09 | BINUH / UNSOH | intermission settlement | charge_id;clearing_document;settlement_date;amount;outstanding_balance |
| REQ10 | BINUH / UNSOH | aviation flight vendor ledger | flight_id;hour;aviation_contract;vendor_invoice;service_date;cost_center;allocation |
| REQ11 | BINUH / UNSOH | personnel and support post rosters | post_id;cost_center;transfer;abolishment;payroll_date;separation_cost;role |
| REQ12 | RSCE | Kuwait shared office closeout | old_client;service_line;last_invoice;balances;post_ids;handover_date |
| REQ13 | RSCE | client cost allocation schedule | client_id;service_line;period;rate;denominator;allocation;approval |
| REQ14 | RSCE | client vs RSCE GL AP AR | allocation_id;RSCE_credit;client_debit;posting_date;period;invoice;settlement;amount |
| REQ15 | RSCE | actual transaction volume and FTE | service_line;projected_volume;actual_volume;time_per_case;FTE;waiting_days;quality |
| REQ16 | RSCE | workforce post unique identifiers | post_id;old_unit;new_unit;abolished;approved_date;actual_date;fund;payroll |
| REQ17 | RSCE | approved finance allocation perimeters | FY2026_27_total;mixed_share_3443200;2027_calendar_SPM_share_3259100;observer_mission_share |
| REQ18 | RSCE | KJSO RSCEx DOS post number match | post_id;former_unit;approved_table;receiving_unit;salary_fund;effective_date;last_payroll;employment_status |

## Required export contract

**Delivery:** One CSV per dataset (UTF-8 with original numeric and date values), or XLSX with distinct named data tabs. Provide a separate dictionary describing each field, data owner, extraction date, source report or Umoja query, the currency, cost centre and fund account definitions, and any filters/exclusions.

**Keys must survive redaction.** Preserve a stable, non-identifying document/asset/position/vendor key so source and receiving records can be joined. At minimum retain transaction/posting date, service period, unique original document ID, amount and currency, reversal/correction flag, original and receiving fund, cost centre, GL account and current record status whenever applicable. Do not replace missing values with zero; indicate *not applicable*, *missing from source*, or *redacted* separately.

**Completeness check:** Provide counts and gross amount totals per month and fund for each export; counts of reversed entries, open commitments, unmatched invoices, outstanding receivables, canceled purchase orders and open asset transfers. Confirm whether the extract includes credits/negative lines, vendor adjustments, service reallocations and transactions posted after the original service period.

**Confidentiality and access:** Use a UN-approved restricted transfer and storage mechanism. Avoid unnecessary names, identification documents, bank details, medical data, exact protected movements and classified locations. If join keys themselves are sensitive, deliver a securely pseudonymized version maintaining a one-to-one token across sending and receiving entities. **Do not transmit real records through the public GitHub repository**, or commit them to GitHub Actions logs, README documents, issues or pull requests.

**Authoritative reviewer:** Mission/RSCE financial controllers and designated asset/HR custodians should confirm each extract's completeness, scope, official classification, and whether the researcher is permitted to access it. A signed access or data-release authorization is required where applicable; this request does not itself grant access.

## What the data will establish

The first audit matches **asset release/receipt** and canceled replacement procurement; the second matches **BINUH payables to UNSOH receivables** and traces settlement plus external supplier costs; the third matches **RSCE client debits to credits** and reconciles client populations, service cost allocations, unique staff positions and KJSO closure. No matched transaction alone proves an incremental net saving until remaining service and transition costs are verified and mandated activity is preserved.

## Reproducibility

The [18-row machine-readable specification](../data/restricted_transaction_request_spec.csv) contains date windows, fields, responsible custodians, deliverable format and safe-handling requirements. The existing [R matcher](../scripts/audit_transaction_ledger.R) runs in an approved secure environment and only validates consistent pairs; actual net savings remain an independent adjudication.
