/* SIMULATIONS TABLE */
CREATE TYPE sim_status AS ENUM ('QUEUED', 'STARTING', 'RUNNING', 'FINISHED', 'ERROR');

CREATE TABLE simulations(
  id SERIAL PRIMARY KEY,
  queued_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (now()),
  start_time TIMESTAMP WITH TIME ZONE DEFAULT NULL,
  end_time TIMESTAMP WITH TIME ZONE DEFAULT NULL,
  status SIM_STATUS NOT NULL DEFAULT 'QUEUED',
  replay_file VARCHAR(256),
  output TEXT NOT NULL DEFAULT ''
);

CREATE FUNCTION sim_status_change() RETURNS TRIGGER AS $sim_sc$
BEGIN
  IF NEW.status = 'RUNNING' THEN
    NEW.start_time := CURRENT_TIMESTAMP;
    NEW.end_time := NULL;
  END IF;

  IF NEW.status = 'FINISHED' OR NEW.status = 'ERROR' THEN
    NEW.end_time := CURRENT_TIMESTAMP;
  END IF;

  RETURN NEW;
END;
$sim_sc$ LANGUAGE plpgsql;

CREATE TRIGGER sim_status_change BEFORE UPDATE ON simulations
  FOR EACH ROW EXECUTE PROCEDURE sim_status_change();


/* SIMULATION_SCORES TABLE */
CREATE TABLE simulation_scores(
  simulation_id INT NOT NULL REFERENCES simulations(id),
  program VARCHAR(64) NOT NULL,
  score INT NOT NULL,
  output TEXT NOT NULL DEFAULT ''
)
