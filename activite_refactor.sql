-- ============================================================
--  Projet 2 — Suivi sportif & fitness
--  Ajout de la table de référence `activite`
--  + refactoring de la table `sessions`
--
--  À exécuter dans phpMyAdmin sur la base `ma_base`
-- ============================================================

USE `ma_base`;

-- ------------------------------------------------------------
-- 1. Création de la table de référence `activite`
--    Contient les 6 activités définies dans le cahier des charges
--    avec leur valeur MET de base (source : OMS / CDC)
-- ------------------------------------------------------------

CREATE TABLE `activite` (
  `id`       int(11)      NOT NULL AUTO_INCREMENT,
  `nom`      varchar(100) NOT NULL,           -- ex. "course", "yoga"
  `met_base` float        NOT NULL,           -- valeur MET standard
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_nom` (`nom`)                 -- évite les doublons de nom
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ------------------------------------------------------------
-- 2. Insertion des 6 activités du cahier des charges
--    (type_id 1–6 correspond à l'index utilisé dans calculs.c)
-- ------------------------------------------------------------

INSERT INTO `activite` (`id`, `nom`, `met_base`) VALUES
  (1, 'course',        8.0),
  (2, 'velo',          6.0),
  (3, 'natation',      7.0),
  (4, 'musculation',   4.0),
  (5, 'yoga',          2.5),
  (6, 'marche_rapide', 4.3);

-- ------------------------------------------------------------
-- 3. Ajout de la colonne `activite_id` dans `sessions`
--    On garde temporairement `type` pour la migration des données
-- ------------------------------------------------------------

ALTER TABLE `sessions`
  ADD COLUMN `activite_id` int(11) NULL
    AFTER `user_id`;

-- ------------------------------------------------------------
-- 4. Migration : remplir activite_id à partir de l'ancienne
--    colonne `type` (si la table avait déjà des données)
-- ------------------------------------------------------------

UPDATE `sessions` s
  JOIN `activite` a ON a.`nom` = s.`type`
  SET s.`activite_id` = a.`id`;

-- ------------------------------------------------------------
-- 5. Rendre activite_id NOT NULL maintenant que c'est rempli
--    puis supprimer l'ancienne colonne `type`
-- ------------------------------------------------------------

ALTER TABLE `sessions`
  MODIFY COLUMN `activite_id` int(11) NOT NULL;

ALTER TABLE `sessions`
  DROP COLUMN `type`;

-- ------------------------------------------------------------
-- 6. Ajout de la contrainte de clé étrangère
--    sessions.activite_id → activite.id
-- ------------------------------------------------------------

ALTER TABLE `sessions`
  ADD CONSTRAINT `fk_activite`
    FOREIGN KEY (`activite_id`)
    REFERENCES `activite` (`id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT;

-- ------------------------------------------------------------
-- Résultat final : schéma complet pour vérification
-- ------------------------------------------------------------

-- Table users (inchangée)
-- CREATE TABLE `users` (
--   `id`        int(11)      NOT NULL AUTO_INCREMENT,
--   `name`      varchar(100) NOT NULL,
--   `weight_kg` float        NOT NULL,
--   `height_m`  float        NOT NULL,
--   `age`       int(11)      DEFAULT NULL,
--   `sex`       enum('M','F') DEFAULT NULL,
--   PRIMARY KEY (`id`)
-- );

-- Table activite (nouvelle)
-- CREATE TABLE `activite` (
--   `id`       int(11)      NOT NULL AUTO_INCREMENT,
--   `nom`      varchar(100) NOT NULL,
--   `met_base` float        NOT NULL,
--   PRIMARY KEY (`id`),
--   UNIQUE KEY `uq_nom` (`nom`)
-- );

-- Table sessions (modifiée : type → activite_id)
-- CREATE TABLE `sessions` (
--   `id`          int(11) NOT NULL AUTO_INCREMENT,
--   `user_id`     int(11) NOT NULL,
--   `activite_id` int(11) NOT NULL,
--   `duration_min` int(11) NOT NULL,
--   `MET`         float   NOT NULL,
--   `date`        date    NOT NULL,
--   `calories`    float   NOT NULL,
--   PRIMARY KEY (`id`),
--   CONSTRAINT `fk_user`     FOREIGN KEY (`user_id`)     REFERENCES `users`   (`id`),
--   CONSTRAINT `fk_activite` FOREIGN KEY (`activite_id`) REFERENCES `activite` (`id`)
-- );
