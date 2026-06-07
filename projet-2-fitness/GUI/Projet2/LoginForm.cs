using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Projet2;

public partial class LoginForm : Form
{
    // On utilise directement ton ApiClient.cs, c'est beaucoup plus propre !
    private readonly ApiClient _apiClient = new ApiClient();

    public LoginForm()
    {
        InitializeComponent();
        
        // Attachement des événements
        this.Load += LoginForm_Load;
        this.loginButton.Click += LoginButton_Click;
        this.newUserButton.Click += NewUserButton_Click;
    }

    private async void LoginForm_Load(object sender, EventArgs e)
    {
        await LoadUsersFromServerAsync();
    }

    /// <summary>
    /// Récupère la liste des utilisateurs en utilisant ton ApiClient
    /// </summary>
    private async Task LoadUsersFromServerAsync()
    {
        try
        {
            // Un seul appel simple grâce à ton architecture
            List<User> users = await _apiClient.GetUsersAsync();
            
            if (users != null && users.Count > 0)
            {
                userComboBox.DataSource = users;
                // Ton Models.cs gère déjà l'affichage grâce à "public override string ToString()"
                // La liste déroulante affichera directement : "Nom (IMC X.X)"
            }
            else
            {
                MessageBox.Show("Aucun utilisateur n'a pu être chargé.", "Information", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Erreur de connexion à l'API : {ex.Message}", "Erreur Serveur", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private void LoginButton_Click(object sender, EventArgs e)
    {
        if (userComboBox.SelectedItem is User selectedUser)
        {
            // On ouvre le Hub au lieu du ProfileForm
            var menu = new MenuForm(selectedUser.Id);
            menu.Show();
            this.Hide();
        }
        else
        {
            MessageBox.Show("Veuillez sélectionner un utilisateur.");
        }
    }

    private void NewUserButton_Click(object sender, EventArgs e)
    {
        MessageBox.Show("Redirection vers la création de profil...", "Nouveau profil", MessageBoxButtons.OK, MessageBoxIcon.Information);
        
        // À décommenter pour la création
         var profileForm = new ProfileForm(null);
         profileForm.Show();
         this.Hide();
    }
}