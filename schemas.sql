--------------------------Tea Bot-------------------------
-- imp

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE SCHEMA IF NOT EXISTS smanager;


CREATE TABLE IF NOT EXISTS smanager.custom_data(
    c_id SERIAL NOT NULL,
    custom_num INTEGER,
    guild_id BIGINT NOT NULL,
    toggle BOOLEAN NOT NULL DEFAULT(TRUE),
    slotlist_ch BIGINT NOT NULL,
    reg_ch BIGINT NOT NULL,
    num_slots INTEGER DEFAULT (25) NOT NULL,
    reserverd_slots INTEGER,
    allowed_slots INTEGER NOT NULL,
    num_correct_mentions INTEGER DEFAULT (1),
    custom_title character varying,
    correct_reg_role BIGINT NOT NULL,
    open_time time without time zone,
    is_registeration_done_today boolean DEFAULT(FALSE),
    is_running BOOLEAN NOT NULL DEFAULT(FALSE),
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



-- tags///////////////////
CREATE TABLE IF NOT EXISTS tags (id SERIAL, name TEXT, content TEXT, owner_id BIGINT, uses INTEGER DEFAULT (0), location_id BIGINT, 
created_at TIMESTAMP DEFAULT (now() at time zone 'utc'), PRIMARY KEY (id));
CREATE INDEX IF NOT EXISTS tags_location_id_idx ON tags (location_id);
CREATE INDEX IF NOT EXISTS tags_name_trgm_idx ON tags USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS tags_name_lower_idx ON tags (LOWER(name));
CREATE UNIQUE INDEX IF NOT EXISTS tags_uniq_idx ON tags (LOWER(name), location_id);

CREATE TABLE IF NOT EXISTS tag_lookup (id SERIAL, name TEXT, location_id BIGINT, owner_id BIGINT, created_at TIMESTAMP DEFAULT (now() at time zone 'utc'), tag_id INTEGER REFERENCES tags (id) ON DELETE CASCADE ON UPDATE NO ACTION, PRIMARY KEY (id));
CREATE INDEX IF NOT EXISTS tag_lookup_name_idx ON tag_lookup (name);
CREATE INDEX IF NOT EXISTS tag_lookup_location_id_idx ON tag_lookup (location_id);
CREATE INDEX IF NOT EXISTS tag_lookup_name_trgm_idx ON tag_lookup USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS tag_lookup_name_lower_idx ON tag_lookup (LOWER(name));
CREATE UNIQUE INDEX IF NOT EXISTS tag_lookup_uniq_idx ON tag_lookup (LOWER(name), location_id);



