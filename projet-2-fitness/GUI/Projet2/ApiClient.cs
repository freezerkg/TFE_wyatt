// ApiClient.cs - Toutes les communications avec l'API Flask
// Aucun calcul ici - uniquement des appels HTTP et deserialisation JSON

using System.Net.Http;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;

namespace Projet2
{
    public class ApiClient
    {
        // ─────────────────────────────────────────────
        // Instance unique partagee dans toute l'application
        // HttpClient ne doit pas etre instancie a chaque appel
        // ─────────────────────────────────────────────
        private static readonly HttpClient _http = new HttpClient
        {
            BaseAddress = new Uri("http://127.0.0.1:5000"),
            Timeout     = TimeSpan.FromSeconds(10)
        };

        private static readonly JsonSerializerOptions _json = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };

        // ─────────────────────────────────────────────
        // UTILISATEURS
        // ─────────────────────────────────────────────

        public async Task<List<User>> GetUsersAsync()
        {
            var response = await _http.GetFromJsonAsync<ApiResponse<List<User>>>("/api/users");
            return response?.Data ?? new List<User>();
        }

        public async Task<User?> GetUserAsync(int userId)
        {
            var response = await _http.GetFromJsonAsync<ApiResponse<User>>($"/api/users/{userId}");
            return response?.Data;
        }

        public async Task<User?> CreateUserAsync(object data)
        {
            var content  = new StringContent(JsonSerializer.Serialize(data),
                           Encoding.UTF8, "application/json");
            var http     = await _http.PostAsync("/api/users", content);
            var response = await http.Content.ReadFromJsonAsync<ApiResponse<User>>(_json);
            return response?.Data;
        }

        public async Task<User?> UpdateUserAsync(int userId, object data)
        {
            var content  = new StringContent(JsonSerializer.Serialize(data),
                           Encoding.UTF8, "application/json");
            var http     = await _http.PutAsync($"/api/users/{userId}", content);
            var response = await http.Content.ReadFromJsonAsync<ApiResponse<User>>(_json);
            return response?.Data;
        }

        // ─────────────────────────────────────────────
        // SEANCES
        // ─────────────────────────────────────────────

        public async Task<List<Session>> GetSessionsAsync(int userId)
        {
            var response = await _http.GetFromJsonAsync<ApiResponse<List<Session>>>(
                $"/api/sessions?user_id={userId}");
            return response?.Data ?? new List<Session>();
        }

        public async Task<Session?> CreateSessionAsync(object sessionData)
        {
            var response = await _http.PostAsJsonAsync("/api/sessions", sessionData);
    
            if (response.IsSuccessStatusCode)
            {
                // On lit l'enveloppe complète, car app.py renvoie : {"status": "ok", "data": ...}
                var result = await response.Content.ReadFromJsonAsync<ApiResponse<Session>>(_json);
        
                // On retourne uniquement l'objet contenu dans "data"
                return result?.Data; 
            }
            else
            {
                var error = await response.Content.ReadAsStringAsync();
                MessageBox.Show($"Erreur API : {error}");
                return null;
            }
        }
        

        // ─────────────────────────────────────────────
        // ACTIVITES
        // ─────────────────────────────────────────────

        public async Task<List<Activite>> GetActivitesAsync()
        {
            var response = await _http.GetFromJsonAsync<ApiResponse<List<Activite>>>("/api/activites");
            return response?.Data ?? new List<Activite>();
        }

        // ─────────────────────────────────────────────
        // STATISTIQUES
        // ─────────────────────────────────────────────

        public async Task<Stats?> GetStatsAsync(int userId)
        {
            var response = await _http.GetFromJsonAsync<ApiResponse<Stats>>(
                $"/api/users/{userId}/stats");
            return response?.Data;
        }

        // ─────────────────────────────────────────────
        // HISTORIQUE IMC
        // ─────────────────────────────────────────────

        public async Task<List<BmiPoint>> GetBmiHistoryAsync(int userId)
        {
            var response = await _http.GetFromJsonAsync<ApiResponse<List<BmiPoint>>>(
                $"/api/users/{userId}/bmi-history");
            return response?.Data ?? new List<BmiPoint>();
        }
    }
}