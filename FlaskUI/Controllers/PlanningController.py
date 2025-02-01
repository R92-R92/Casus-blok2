from Controllers.DatabaseController import DatabaseController

class PlanningController:
    def __init__(self):
        self.db = DatabaseController()

    def get_all_reservations(self):
        return self.db.fetch_all("Reserveringen")

    def get_reservation_by_id(self, reservation_id):
        return self.db.fetch_by_condition("Reserveringen", {"Reservering_id": reservation_id})

    def create_reservation(self, gebruiker_id, datum, tijd, beschrijving):
        return self.db.insert("Reserveringen", {
            "Gebruiker_id": gebruiker_id,
            "Datum": datum,
            "Tijd": tijd,
            "Beschrijving": beschrijving
        })

    def update_reservation(self, reservation_id, datum, tijd, beschrijving):
        return self.db.update("Reserveringen", {
            "Datum": datum,
            "Tijd": tijd,
            "Beschrijving": beschrijving
        }, {"Reservering_id": reservation_id})

    def delete_reservation(self, reservation_id):
        return self.db.delete("Reserveringen", {"Reservering_id": reservation_id})
