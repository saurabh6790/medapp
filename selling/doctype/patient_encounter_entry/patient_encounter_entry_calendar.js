// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
wn.views.calendar["Patient Encounter Entry"] = {
	field_map: {
		"proj":"encounter",
		"start": "start_time",
		"end": "end_time",
		"id": "name",
		"title": wn._("study"),
		"allDay": "allDay",
		"status": "status"
	},
	style_map: {
		"Confirmed": "success",
		"Waiting": "info",
		"Canceled": "warning"
	},
	get_events_method: "selling.doctype.patient_encounter_entry.patient_encounter_entry.get_events"
}