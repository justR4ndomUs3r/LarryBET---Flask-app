-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Wersja serwera:               10.6.5-MariaDB - mariadb.org binary distribution
-- Serwer OS:                    Win64
-- HeidiSQL Wersja:              11.3.0.6295
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Zrzut struktury bazy danych larrybet
CREATE DATABASE IF NOT EXISTS `larrybet` /*!40100 DEFAULT CHARACTER SET latin7 */;
USE `larrybet`;

-- Zrzut struktury procedura larrybet.doladuj_konto
DELIMITER //
CREATE PROCEDURE `doladuj_konto`(
	IN `Kwota` INT,
	IN `vIdPortfela` INT
)
    MODIFIES SQL DATA
BEGIN
UPDATE Portfele
SET stan_konta = stan_konta + kwota
WHERE id_portfela = vIdPortfela;
END//
DELIMITER ;

-- Zrzut struktury tabela larrybet.druzyny
CREATE TABLE IF NOT EXISTS `druzyny` (
  `id_druzyny` int(6) NOT NULL AUTO_INCREMENT,
  `nazwa` varchar(50) NOT NULL,
  `kraj` varchar(50) NOT NULL,
  `stadion` varchar(50) NOT NULL,
  PRIMARY KEY (`id_druzyny`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=latin7;

-- Zrzucanie danych dla tabeli larrybet.druzyny: ~12 rows (około)
/*!40000 ALTER TABLE `druzyny` DISABLE KEYS */;
INSERT INTO `druzyny` (`id_druzyny`, `nazwa`, `kraj`, `stadion`) VALUES
	(1, 'Real Madryt', 'Hiszpania', 'Santiago Bernabeu'),
	(2, 'FC Barcelona', 'Hiszpania', 'Camp Nou'),
	(3, 'Atletico Madryt', 'Hiszpania', 'Vanda Metropolitano'),
	(4, 'Sevilla CF', 'Hiszpania', 'Ramon Sanchez-Pizjuan'),
	(6, 'Athletic Bilbao', 'Hiszpania', 'San Mames'),
	(7, 'Manchester United', 'Anglia', 'Old Trafford'),
	(8, 'Liverpool', 'Anglia', 'Anfield Road'),
	(9, 'Manchester City', 'Anglia', 'Etihad Stadium'),
	(11, 'Tottenham Hotspur', 'Anglia', 'Tottenham Hotspur Stadium'),
	(12, 'Arsenal', 'Anglia', 'Emirates Stadium'),
	(14, 'AC Milan', 'Włochy', 'San Siro'),
	(19, 'KKS Lech Poznań', 'Polska', 'Bułgarska');
/*!40000 ALTER TABLE `druzyny` ENABLE KEYS */;

-- Zrzut struktury funkcja larrybet.licz_cene
DELIMITER //
CREATE FUNCTION `licz_cene`(`vIdOferty` INT,
	`vIle` INT
) RETURNS int(11)
BEGIN
RETURN (SELECT (cena * vIle) FROM oferty WHERE id_oferty = vIdOferty);
END//
DELIMITER ;

-- Zrzut struktury funkcja larrybet.licz_monety
DELIMITER //
CREATE FUNCTION `licz_monety`(`vIdOferty` INT,
	`vIle` INT
) RETURNS int(11)
    DETERMINISTIC
BEGIN
SELECT (liczba_monet * vIle) INTO @res FROM oferty WHERE id_oferty = vIdOferty;
RETURN @res;
END//
DELIMITER ;

-- Zrzut struktury tabela larrybet.ligi
CREATE TABLE IF NOT EXISTS `ligi` (
  `id_ligi` int(6) NOT NULL AUTO_INCREMENT,
  `nazwa` varchar(50) NOT NULL,
  PRIMARY KEY (`id_ligi`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin7;

-- Zrzucanie danych dla tabeli larrybet.ligi: ~5 rows (około)
/*!40000 ALTER TABLE `ligi` DISABLE KEYS */;
INSERT INTO `ligi` (`id_ligi`, `nazwa`) VALUES
	(1, 'LaLiga'),
	(2, 'Champions League'),
	(3, 'Premier League'),
	(4, 'Liga Europy'),
	(7, 'B klasa');
/*!40000 ALTER TABLE `ligi` ENABLE KEYS */;

-- Zrzut struktury tabela larrybet.ligi_druzyny
CREATE TABLE IF NOT EXISTS `ligi_druzyny` (
  `id_ligi` int(6) NOT NULL,
  `id_druzyny` int(6) NOT NULL,
  PRIMARY KEY (`id_ligi`,`id_druzyny`),
  KEY `ligi_druzyny_ibfk_2` (`id_druzyny`),
  CONSTRAINT `ligi_druzyny_ibfk_1` FOREIGN KEY (`id_ligi`) REFERENCES `ligi` (`id_ligi`) ON DELETE CASCADE,
  CONSTRAINT `ligi_druzyny_ibfk_2` FOREIGN KEY (`id_druzyny`) REFERENCES `druzyny` (`id_druzyny`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin7;

-- Zrzucanie danych dla tabeli larrybet.ligi_druzyny: ~17 rows (około)
/*!40000 ALTER TABLE `ligi_druzyny` DISABLE KEYS */;
INSERT INTO `ligi_druzyny` (`id_ligi`, `id_druzyny`) VALUES
	(1, 1),
	(1, 2),
	(1, 3),
	(1, 4),
	(1, 6),
	(2, 1),
	(2, 2),
	(2, 3),
	(2, 4),
	(2, 7),
	(2, 8),
	(2, 9),
	(3, 7),
	(3, 8),
	(3, 9),
	(3, 11),
	(4, 14);
/*!40000 ALTER TABLE `ligi_druzyny` ENABLE KEYS */;

-- Zrzut struktury tabela larrybet.mecze
CREATE TABLE IF NOT EXISTS `mecze` (
  `id_meczu` int(6) NOT NULL AUTO_INCREMENT,
  `data_meczu` date NOT NULL,
  `kurs_gospodarz` int(10) NOT NULL,
  `kurs_gosc` int(10) NOT NULL,
  `kurs_remis` int(10) NOT NULL,
  `gospodarz` int(6) NOT NULL,
  `gosc` int(6) NOT NULL,
  `liga` int(6) NOT NULL,
  PRIMARY KEY (`id_meczu`),
  KEY `mecze_ibfk_1` (`gospodarz`),
  KEY `mecze_ibfk_2` (`gosc`),
  KEY `mecze_ibfk_3` (`liga`),
  CONSTRAINT `mecze_ibfk_1` FOREIGN KEY (`gospodarz`) REFERENCES `druzyny` (`id_druzyny`) ON DELETE CASCADE,
  CONSTRAINT `mecze_ibfk_2` FOREIGN KEY (`gosc`) REFERENCES `druzyny` (`id_druzyny`) ON DELETE CASCADE,
  CONSTRAINT `mecze_ibfk_3` FOREIGN KEY (`liga`) REFERENCES `ligi` (`id_ligi`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin7;

-- Zrzucanie danych dla tabeli larrybet.mecze: ~6 rows (około)
/*!40000 ALTER TABLE `mecze` DISABLE KEYS */;
INSERT INTO `mecze` (`id_meczu`, `data_meczu`, `kurs_gospodarz`, `kurs_gosc`, `kurs_remis`, `gospodarz`, `gosc`, `liga`) VALUES
	(2, '2022-02-11', 2, 7, 4, 1, 2, 1),
	(3, '2022-02-12', 3, 4, 2, 3, 4, 1),
	(5, '2022-02-12', 2, 2, 2, 7, 9, 3),
	(6, '2022-02-11', 2, 4, 3, 12, 11, 3),
	(7, '2022-02-20', 4, 3, 2, 9, 1, 2),
	(11, '2022-12-12', 2, 2, 2, 1, 4, 1);
/*!40000 ALTER TABLE `mecze` ENABLE KEYS */;

-- Zrzut struktury tabela larrybet.oferty
CREATE TABLE IF NOT EXISTS `oferty` (
  `id_oferty` int(6) NOT NULL AUTO_INCREMENT,
  `nazwa` varchar(50) NOT NULL,
  `liczba_monet` int(10) NOT NULL,
  `cena` decimal(10,0) NOT NULL,
  PRIMARY KEY (`id_oferty`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin7;

-- Zrzucanie danych dla tabeli larrybet.oferty: ~3 rows (około)
/*!40000 ALTER TABLE `oferty` DISABLE KEYS */;
INSERT INTO `oferty` (`id_oferty`, `nazwa`, `liczba_monet`, `cena`) VALUES
	(1, 'DYCHA', 10, 25),
	(2, 'Double D', 20, 40),
	(4, 'SPRZEDAZ', 1, 2);
/*!40000 ALTER TABLE `oferty` ENABLE KEYS */;

-- Zrzut struktury tabela larrybet.portfele
CREATE TABLE IF NOT EXISTS `portfele` (
  `id_portfela` int(6) NOT NULL AUTO_INCREMENT,
  `stan_konta` int(10) NOT NULL,
  `dane_do_rozliczen` varchar(50) NOT NULL,
  `wlasciciel` int(6) NOT NULL,
  `nazwa` varchar(50) NOT NULL,
  PRIMARY KEY (`id_portfela`),
  KEY `portfele_ibfk_1` (`wlasciciel`),
  CONSTRAINT `portfele_ibfk_1` FOREIGN KEY (`wlasciciel`) REFERENCES `uzytkownicy` (`id_uzytk`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin7;

-- Zrzucanie danych dla tabeli larrybet.portfele: ~2 rows (około)
/*!40000 ALTER TABLE `portfele` DISABLE KEYS */;
INSERT INTO `portfele` (`id_portfela`, `stan_konta`, `dane_do_rozliczen`, `wlasciciel`, `nazwa`) VALUES
	(3, 200, '1234 4321 1234 4321 0000 2222', 8, 'Portfelik'),
	(11, 0, '123123125235636', 8, 'Portfel2');
/*!40000 ALTER TABLE `portfele` ENABLE KEYS */;

-- Zrzut struktury tabela larrybet.transakcje
CREATE TABLE IF NOT EXISTS `transakcje` (
  `id_transakcji` int(6) NOT NULL AUTO_INCREMENT,
  `data_transakcji` date NOT NULL DEFAULT curdate(),
  `stan_konta_przed` int(10) NOT NULL,
  `stan_konta_po` int(10) NOT NULL,
  `kwota` int(11) NOT NULL,
  `rodzaj` int(6) DEFAULT NULL,
  `portfel_transakcji` int(6) DEFAULT NULL,
  PRIMARY KEY (`id_transakcji`) USING BTREE,
  KEY `transakcje_ibfk_2` (`portfel_transakcji`) USING BTREE,
  KEY `transakcje_ibfk_1` (`rodzaj`) USING BTREE,
  CONSTRAINT `transakcje_ibfk_1` FOREIGN KEY (`rodzaj`) REFERENCES `oferty` (`id_oferty`) ON DELETE SET NULL,
  CONSTRAINT `transakcje_ibfk_2` FOREIGN KEY (`portfel_transakcji`) REFERENCES `portfele` (`id_portfela`) ON DELETE SET NULL ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=latin7;

-- Zrzucanie danych dla tabeli larrybet.transakcje: ~12 rows (około)
/*!40000 ALTER TABLE `transakcje` DISABLE KEYS */;
INSERT INTO `transakcje` (`id_transakcji`, `data_transakcji`, `stan_konta_przed`, `stan_konta_po`, `kwota`, `rodzaj`, `portfel_transakcji`) VALUES
	(8, '2022-01-10', 0, 10, 25, 1, 3),
	(9, '2022-01-10', 10, 30, 40, 2, 3),
	(15, '2022-01-14', 125, 135, 25, 1, 3),
	(16, '2022-01-14', 135, 145, 25, 1, 3),
	(17, '2022-01-14', 145, 140, 10, 4, 3),
	(18, '2022-01-14', 140, 150, 25, 1, 3),
	(19, '2022-01-14', 150, 170, 50, 1, 3),
	(20, '2022-01-14', 0, 10, 25, 1, NULL),
	(21, '2022-01-14', 0, 10, 25, 1, NULL),
	(22, '2022-01-14', 0, 250, 400, NULL, NULL),
	(23, '2022-01-14', 350, 250, 200, 4, NULL),
	(24, '2022-01-20', 160, 60, 200, 4, 3);
/*!40000 ALTER TABLE `transakcje` ENABLE KEYS */;

-- Zrzut struktury tabela larrybet.uzytkownicy
CREATE TABLE IF NOT EXISTS `uzytkownicy` (
  `id_uzytk` int(6) NOT NULL AUTO_INCREMENT,
  `email` varchar(50) NOT NULL,
  `haslo` varchar(100) NOT NULL,
  `pesel` varchar(50) DEFAULT NULL,
  `imie` varchar(50) DEFAULT NULL,
  `nazwisko` varchar(50) DEFAULT NULL,
  `telefon` varchar(50) DEFAULT NULL,
  `uprawnienia` varchar(1) NOT NULL CHECK (`uprawnienia` in ('K','M','A')),
  PRIMARY KEY (`id_uzytk`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin7;

-- Zrzucanie danych dla tabeli larrybet.uzytkownicy: ~5 rows (około)
/*!40000 ALTER TABLE `uzytkownicy` DISABLE KEYS */;
INSERT INTO `uzytkownicy` (`id_uzytk`, `email`, `haslo`, `pesel`, `imie`, `nazwisko`, `telefon`, `uprawnienia`) VALUES
	(5, 'admin@admin', 'sha256$9cbmvSTvdqzQzCQt$46ea6069c8186535a7ce12019cc5f1abc3983ffaf77e29a0c15791e4acb920db', NULL, 'Admin', NULL, NULL, 'A'),
	(6, 'pracownik@larrybet.com', 'sha256$8T0IeySJCF7Q93Zm$dc71fb8810d056ba5675dba529a962134bed63584f60b4c0ae4b88a8e57ceb8c', '11111111111', 'Grzegorz', 'Nowak', '111111111', 'M'),
	(8, 'danielsz25@wp.pl', 'sha256$yOdYsxcgZhUPQ7gZ$3cc0efbba7312ec7386bfa4d10179b18c09ca1d2879fd6df2463ffc76ad4abb8', '99999989876', 'Mikołaj', 'asd', '76543218', 'K'),
	(11, 'adam@wp.pl', 'sha256$mvhY02UDLgossO5M$b2d64d3436f08559b6ba23d1fd36b354c9a4fbea54abe44c29d382e61d7d51b2', '22222222222', 'Adam', 'Adam', '111111222', 'K'),
	(15, 'Krzys@pracownik', 'sha256$D41q4HMgU4zYsWkG$427c56da11245c368c3c3cfae9bc927cce174414bdc3c458435b0991f21fc79f', '12311232312', 'Krzysio', 'Krzysztowski', '777666555', 'M');
/*!40000 ALTER TABLE `uzytkownicy` ENABLE KEYS */;

-- Zrzut struktury tabela larrybet.wyniki
CREATE TABLE IF NOT EXISTS `wyniki` (
  `id_wyniku` int(6) NOT NULL AUTO_INCREMENT,
  `mecz` int(6) NOT NULL,
  `zwyciezca` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_wyniku`),
  KEY `wyniki_ibfk_1` (`mecz`),
  CONSTRAINT `wyniki_ibfk_1` FOREIGN KEY (`mecz`) REFERENCES `mecze` (`id_meczu`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin7;

-- Zrzucanie danych dla tabeli larrybet.wyniki: ~2 rows (około)
/*!40000 ALTER TABLE `wyniki` DISABLE KEYS */;
INSERT INTO `wyniki` (`id_wyniku`, `mecz`, `zwyciezca`) VALUES
	(20, 7, 0),
	(21, 2, 2);
/*!40000 ALTER TABLE `wyniki` ENABLE KEYS */;

-- Zrzut struktury tabela larrybet.zaklady
CREATE TABLE IF NOT EXISTS `zaklady` (
  `id_zakladu` int(6) NOT NULL AUTO_INCREMENT,
  `typ` int(1) NOT NULL CHECK (`typ` in (0,1,2)),
  `monety_postawione` int(10) NOT NULL,
  `status` varchar(1) NOT NULL CHECK (`status` in ('R','N')),
  `wygrana` int(10) NOT NULL,
  `data_zakladu` date NOT NULL DEFAULT curdate(),
  `portfel` int(6) NOT NULL,
  `mecz` int(6) NOT NULL,
  PRIMARY KEY (`id_zakladu`),
  KEY `mecz` (`mecz`),
  KEY `zaklady_ibfk_1` (`portfel`),
  CONSTRAINT `zaklady_ibfk_1` FOREIGN KEY (`portfel`) REFERENCES `portfele` (`id_portfela`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin7;

-- Zrzucanie danych dla tabeli larrybet.zaklady: ~5 rows (około)
/*!40000 ALTER TABLE `zaklady` DISABLE KEYS */;
INSERT INTO `zaklady` (`id_zakladu`, `typ`, `monety_postawione`, `status`, `wygrana`, `data_zakladu`, `portfel`, `mecz`) VALUES
	(2, 0, 15, 'R', 30, '2022-01-11', 3, 1),
	(3, 2, 5, 'R', 0, '2022-01-11', 3, 1),
	(4, 2, 10, 'R', 70, '2022-01-12', 3, 2),
	(6, 2, 5, 'R', 100, '2022-01-13', 3, 8),
	(11, 2, 10, 'R', 70, '2022-01-20', 3, 2);
/*!40000 ALTER TABLE `zaklady` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
