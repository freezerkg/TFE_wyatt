namespace Projet2
{
    partial class MenuForm
    {
        private System.ComponentModel.IContainer components = null;
        private System.Windows.Forms.Button btnModifierProfil;
        private System.Windows.Forms.Button btnAjoutSeance;
        private System.Windows.Forms.Button btnDashboard;
        private System.Windows.Forms.Button btnBack;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null)) components.Dispose();
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.btnModifierProfil = new System.Windows.Forms.Button { Text = "Modifier Profil", Location = new System.Drawing.Point(50, 30), Size = new System.Drawing.Size(200, 40) };
            this.btnAjoutSeance = new System.Windows.Forms.Button { Text = "Ajouter une Séance", Location = new System.Drawing.Point(50, 80), Size = new System.Drawing.Size(200, 40) };
            this.btnBack = new System.Windows.Forms.Button { Text = "Déconnexion", Location = new System.Drawing.Point(50, 150), Size = new System.Drawing.Size(200, 30) };

            // Ajout des événements
            this.btnModifierProfil.Click += btnModifierProfil_Click;
            this.btnAjoutSeance.Click += btnAjoutSeance_Click;
            this.btnBack.Click += btnBack_Click;

            this.ClientSize = new System.Drawing.Size(300, 220);
            this.Controls.AddRange(new System.Windows.Forms.Control[] { btnModifierProfil, btnAjoutSeance, btnBack });
            this.Text = "Menu Principal";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
        }
    }
}