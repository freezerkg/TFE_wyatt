// Models.cs - Classes de donnees du projet Fitness
// Chaque classe correspond exactement au format JSON retourne par l'API Flask

using System.Text.Json.Serialization;

namespace Projet2
{
    // ─────────────────────────────────────────────
    // Enveloppe generique de toutes les reponses API
    // {"status": "ok", "data": ...}
    // ─────────────────────────────────────────────
    public class ApiResponse<T>
    {
        [JsonPropertyName("status")]
        public string Status { get; set; } = "";

        [JsonPropertyName("data")]
        public T? Data { get; set; }
    }

    // ─────────────────────────────────────────────
    // Utilisateur
    // ─────────────────────────────────────────────
    public class User
    {
        [JsonPropertyName("id")]
        public int Id { get; set; }

        [JsonPropertyName("name")]
        public string Name { get; set; } = "";

        [JsonPropertyName("weight_kg")]
        public float WeightKg { get; set; }

        [JsonPropertyName("height_m")]
        public float HeightM { get; set; }

        [JsonPropertyName("age")]
        public int? Age { get; set; }

        [JsonPropertyName("sex")]
        public string? Sex { get; set; }

        [JsonPropertyName("bmi")]
        public float Bmi { get; set; }

        [JsonPropertyName("bmi_category")]
        public string BmiCategory { get; set; } = "";

        // Affichage dans les ComboBox
        public override string ToString() => $"{Name} (IMC {Bmi:F1})";
    }

    // ─────────────────────────────────────────────
    // Seance sportive
    // ─────────────────────────────────────────────
    public class Session
    {
        [JsonPropertyName("id")]
        public int Id { get; set; }

        [JsonPropertyName("user_id")]
        public int UserId { get; set; }

        [JsonPropertyName("activite_id")]
        public int ActiviteId { get; set; }

        [JsonPropertyName("activite_nom")]
        public string ActiviteNom { get; set; } = "";

        [JsonPropertyName("duration_min")]
        public int DurationMin { get; set; }

        [JsonPropertyName("met")]
        public float Met { get; set; }

        [JsonPropertyName("date")]
        public string Date { get; set; } = "";

        [JsonPropertyName("calories")]
        public float Calories { get; set; }
    }

    // ─────────────────────────────────────────────
    // Activite sportive
    // ─────────────────────────────────────────────
    public class Activite
    {
        [JsonPropertyName("id")]
        public int Id { get; set; }

        [JsonPropertyName("nom")]
        public string Nom { get; set; } = "";

        [JsonPropertyName("met_base")]
        public float MetBase { get; set; }

        // Affichage dans les ComboBox
        public override string ToString() => Nom;
    }

    // ─────────────────────────────────────────────
    // Statistiques hebdomadaires / mensuelles
    // ─────────────────────────────────────────────
    public class PeriodStats
    {
        [JsonPropertyName("total_min")]
        public int TotalMin { get; set; }

        [JsonPropertyName("total_kcal")]
        public float TotalKcal { get; set; }

        [JsonPropertyName("count")]
        public int Count { get; set; }
    }

    public class Stats
    {
        [JsonPropertyName("weekly")]
        public PeriodStats Weekly { get; set; } = new();

        [JsonPropertyName("monthly")]
        public PeriodStats Monthly { get; set; } = new();
    }

    // ─────────────────────────────────────────────
    // Point d'historique IMC
    // ─────────────────────────────────────────────
    public class BmiPoint
    {
        [JsonPropertyName("date")]
        public string Date { get; set; } = "";

        [JsonPropertyName("bmi")]
        public float Bmi { get; set; }
    }
}