--------------------------Tea Bot-------------------------
-- imp

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE SCHEMA IF NOT EXISTS smanager;


CREATE TABLE IF NOT EXISTS smanager.custom_data(
    c_id SERIAL NOT NULL,
    custom_num INTEGER,
    guild_id BIGINT,
    toggle BOOLEAN DEFAULT(TRUE),
    slotlist_ch BIGINT,
    reg_ch BIGINT,
    num_slots INTEGER DEFAULT (25) ,
    reserverd_slots INTEGER,
    allowed_slots INTEGER,
    num_correct_mentions INTEGER DEFAULT (1),
    custom_title character varying,
    correct_reg_role BIGINT,
    ping_role BIGINT,
    open_role BIGINT,
    open_time time without time zone,
    close_time time without time zone,
    -- autoclean_time time without time zone DEFAULT('00:15:00'),
    is_registeration_done_today boolean DEFAULT(FALSE),
    is_running BOOLEAN DEFAULT(FALSE),
    auto_clean BOOLEAN DEFAULT(FALSE),
    open_on_sunday BOOLEAN DEFAULT(TRUE),
    open_on_monday BOOLEAN DEFAULT(TRUE),
    open_on_tuesday BOOLEAN DEFAULT(TRUE),
    open_on_wednesday BOOLEAN DEFAULT(TRUE),
    open_on_thursday BOOLEAN DEFAULT(TRUE),
    open_on_friday BOOLEAN DEFAULT(TRUE),
    open_on_saturday BOOLEAN DEFAULT(TRUE),
    team_names character varying[],
    auto_slot_list_send BOOLEAN DEFAULT(FALSE),
    auto_delete_on_reject BOOLEAN DEFAULT(FALSE),
    open_message_embed character varying DEFAULT('{
  "title": ":tools: **Registartion Opened** :tools:",
  "description": "Total Slots = <<available_slots>>/<<total_slots>>[<<reserved_slots>>]\\n\nMinimum Mentions = <<mentions_required>>\n",
  "color": 53380
}'),
    close_message_embed character varying DEFAULT('{
  "description": ":lock: | **__Registration Is Closed Now.__**",
  "color": 53380
}'),
    -- slot_list_embed character varying DEFAULT(''),
    PRIMARY KEY(c_id)
);

CREATE TABLE IF NOT EXISTS smanager.tag_check(
    guild_id BIGINT NOT NULL,
    ch_id BIGINT NOT NULL,
    toggle BOOLEAN DEFAULT(TRUE),
    mentions_required INTEGER,
    PRIMARY KEY (guild_id)
);

CREATE TABLE IF NOT EXISTS server_configs(
    guild_id BIGINT NOT NULL,
    is_bot_setuped BOOLEAN DEFAULT(FALSE),
    scrims_manager BOOLEAN DEFAULT(FALSE),
    max_customs INTEGER DEFAULT(7),
    custom_setuped INTEGER DEFAULT(0),
    autorole_toggle BOOLEAN DEFAULT(FALSE),
    autorole_bot_toggle BOOLEAN DEFAULT(FALSE),
    autorole_human_toggle BOOLEAN DEFAULT(FALSE),
    autorole_human BIGINT ,
    autorole_bot BIGINT,
    is_premium BOOLEAN,
    automeme_toogle BOOLEAN DEFAULT(FALSE),
    automeme_channel_id BIGINT,
    PRIMARY KEY (guild_id)
);


CREATE TABLE IF NOT EXISTS brodcast(
    guild_id BIGINT NOT NULL,
    channel_id BIGINT,
    PRIMARY KEY (guild_id)
);





