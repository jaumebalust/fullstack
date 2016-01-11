-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

drop database if exists tournament;

create database tournament;

\c tournament;

DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS matches;

CREATE TABLE players (   
	ID  BIGSERIAL PRIMARY KEY NOT NULL,
   NAME           TEXT      NOT NULL,
   WINS INT NOT NULL,
   MATCHES_PLAYED INT NOT NULL);

CREATE TABLE matches (   
	ID  BIGSERIAL PRIMARY KEY NOT NULL,
   ID_PLAYER1           INT      NOT NULL,
   
   ID_PLAYER2          INT      NOT NULL,
   
   OUTCOME INT NOT NULL);



